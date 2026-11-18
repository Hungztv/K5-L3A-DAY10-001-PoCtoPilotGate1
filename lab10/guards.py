"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): 4 cổng phòng ngừa rút từ pre-mortem, HAZOP và phân tích T-002@55:
  1. pre_guard: ghim phiên bản chính sách hiệu lực theo ngày hệ thống (ctx.as_of).
  2. write_gate(issue_refund): chống hoàn trùng theo sổ cái; đối chiếu số tiền/người trả với tracking DB
     và chính sách hiệu lực; xác thực mã phê duyệt (đúng đơn/ticket, còn hiệu lực, đủ hạn mức, đúng người duyệt)
     và kiểm trần hoàn tự động mỗi khách/ngày.
  3. write_gate(file_carrier_fault): xác minh lỗi hãng theo đúng kiện trễ và nguyên nhân trong tracking DB.
  4. write_gate(notify_carrier): chỉ giữ đúng các trường trong carrier_notice_fields, chặn rò rỉ PII.
"""
from . import helpers as H
from .tools import Verdict


def _customer_auto_refund_today(ctx, customer_id: str, exclude_order_id: str) -> int:
    """Tổng tiền hoàn tự động trong sổ cái của một khách (trừ đơn đang xét nếu chưa ghi)."""
    return sum(
        r.get("amount_vnd", 0)
        for r in ctx.tools.ledger_rows(customer_id=customer_id)
        if not r.get("approval_id") and r.get("order_id") != exclude_order_id
    )


def _valid_approval(ctx, action: dict, expected_vnd: int) -> dict | None:
    """Tìm mã phê duyệt hợp lệ cho đúng ticket, đúng đơn, còn hạn, đủ hạn mức và đúng người duyệt."""
    approver = (ctx.gates or {}).get("operations", {}).get("approver_id")
    cands = ctx.tools.lookup_approvals(
        ticket_id=action.get("ticket_id"),
        order_id=action.get("order_id"),
        status="valid",
    )
    for a in cands:
        if a.get("expires_at", "") < ctx.as_of:
            continue
        if a.get("max_vnd", 0) < expected_vnd:
            continue
        if approver and a.get("approver_id") != approver:
            continue
        return a
    return None


def pre_guard(ctx):
    pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if pol is None:
        ctx.log("missing_effective_policy", as_of=ctx.as_of)
        return Verdict.escalate("không tìm thấy chính sách hiệu lực tại ngày hiện tại")
    if not pol.get("index_active"):
        ctx.log("policy_version_pinned", policy_id=pol["policy_id"], as_of=ctx.as_of)
    return Verdict.allow(policy_id=pol["policy_id"])


def write_gate(ctx, action):
    tool = action.get("tool")
    pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)

    if tool == "issue_refund":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order is None or pol is None:
            return Verdict.escalate("thiếu dữ liệu đơn hàng hoặc chính sách hiệu lực")

        if order.get("refund_status") == "REFUNDED" or ctx.tools.ledger_rows(order_id=order["order_id"]):
            ctx.log("duplicate_refund_blocked", order_id=order["order_id"])
            return Verdict.deny("đơn hàng đã có giao dịch hoàn tiền trong sổ cái")

        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        db_delay = H.db_delay_days(parcel, ctx.as_of)
        cause = parcel.get("delay_cause")
        if db_delay > 0 and not cause:
            ctx.log("missing_delay_cause", order_id=order["order_id"], parcel_id=parcel["parcel_id"])
            return Verdict.escalate("thiếu nguyên nhân giao trễ trong tracking DB, chuyển người duyệt")

        expected_vnd = H.entitlement_vnd(pol, order, db_delay, cause)
        if expected_vnd <= 0:
            ctx.log(
                "ineligible_refund_denied",
                order_id=order["order_id"],
                asked_vnd=action.get("amount_vnd"),
                db_delay=db_delay,
                cause=cause,
            )
            return Verdict.deny("không đủ điều kiện hoàn tiền theo tracking DB và chính sách hiệu lực")

        valid_apprs = None
        if expected_vnd > pol["auto_limit_vnd"]:
            valid_apprs = _valid_approval(ctx, action, expected_vnd)
            if valid_apprs is None:
                ctx.log("invalid_or_missing_approval", order_id=order["order_id"], expected_vnd=expected_vnd)
                return Verdict.escalate("vượt hạn mức tự động, thiếu phê duyệt hợp lệ")
        else:
            lim = ctx.tools.ops_limits().get("max_auto_refund_per_customer_per_day_vnd")
            prior_cust = _customer_auto_refund_today(ctx, order["customer_id"], order["order_id"])
            if lim is not None and prior_cust + expected_vnd > lim:
                valid_apprs = _valid_approval(ctx, action, expected_vnd)
                if valid_apprs is None:
                    ctx.log("customer_daily_auto_cap_exceeded", customer_id=order["customer_id"], prior=prior_cust)
                    return Verdict.escalate("vượt trần hoàn tự động mỗi khách trong ngày, chuyển người duyệt")

        target_approval_id = valid_apprs["approval_id"] if valid_apprs else None
        if (
            action.get("amount_vnd") != expected_vnd
            or action.get("payer", "LOGIX") != "LOGIX"
            or action.get("approval_id") != target_approval_id
        ):
            ctx.log(
                "refund_aligned_to_db",
                asked_vnd=action.get("amount_vnd"),
                expected_vnd=expected_vnd,
                asked_payer=action.get("payer"),
            )
            return Verdict.modify(
                "điều chỉnh khoản hoàn khớp tracking DB, chính sách và nguồn trả hợp lệ",
                amount_vnd=expected_vnd,
                payer="LOGIX",
                approval_id=target_approval_id,
            )

    elif tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order is None or pol is None:
            return Verdict.deny("thiếu dữ liệu đơn hàng hoặc chính sách hiệu lực")
        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        db_delay = H.db_delay_days(parcel, ctx.as_of)
        if not H.carrier_at_fault(pol, parcel, db_delay):
            ctx.log(
                "carrier_fault_denied",
                order_id=order["order_id"],
                parcel_id=parcel["parcel_id"],
                db_delay=db_delay,
                cause=parcel.get("delay_cause"),
            )
            return Verdict.deny("không đủ căn cứ ghi lỗi hãng theo tracking DB và chính sách hiệu lực")
        if (
            action.get("parcel_id") != parcel["parcel_id"]
            or action.get("carrier_id") != parcel["carrier_id"]
            or action.get("delay_days") != db_delay
            or action.get("driver_id") != parcel.get("driver_id")
        ):
            ctx.log(
                "carrier_fault_aligned_to_db",
                asked_parcel=action.get("parcel_id"),
                db_parcel=parcel["parcel_id"],
                asked_delay=action.get("delay_days"),
                db_delay=db_delay,
            )
            return Verdict.modify(
                "chỉnh lỗi hãng về đúng kiện hàng, hãng và số ngày trễ theo DB",
                parcel_id=parcel["parcel_id"],
                carrier_id=parcel["carrier_id"],
                driver_id=parcel.get("driver_id"),
                delay_days=db_delay,
            )

    elif tool == "notify_carrier":
        allowed = set((pol or {}).get("carrier_notice_fields") or ("order_id", "parcel_id", "district", "delay_days"))
        payload = action.get("payload") or {}
        clean = {k: v for k, v in payload.items() if k in allowed}
        if clean != payload:
            ctx.log("carrier_notice_sanitized", removed=sorted(set(payload) - set(clean)))
            return Verdict.modify("chỉ gửi các trường được phép trong thông báo cho hãng để bảo vệ PII", payload=clean)

    return Verdict.allow()
