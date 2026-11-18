# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): `001`
- Lớp: `L3A`
- Repo của bàn: `K5-L3A-DAY10-001-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): Chưa có *(nghỉ học buổi trên lớp, chưa có gói `incidents/Sx` từ Lab Coach)*

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Dương Mạnh Hùng | 2A202603431 | Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (làm cá nhân toàn bộ 3 vai) | x |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên: `["DuongManhHung-2A202603431"]`.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## DuongManhHung-2A202603431

### Phần việc phụ trách

Làm cá nhân, đảm nhiệm toàn bộ cả 3 vai trong bàn:
- **Sản phẩm và kinh doanh:** Phiếu A (A1–A5), `config/acceptance_criteria.json`, Phiếu B (B3, B6, B7.4, B8).
- **Kỹ sư cổng:** Chạy lệnh `eval`, `trace`, `gate`, `checkpoint`, `check_submission`; viết 4 cổng phòng ngừa trong `lab10/guards.py`; Phiếu A (A2 câu 1.3), Phiếu B (B0–B2, B7.1–B7.3).
- **Vận hành và pháp lý:** `config/operating_gates.json` (mục `operations`, `legal`), `submission/submission.json`, Phiếu A (A1 câu 1.2, A2 câu 1.4), Phiếu B (B4–B5, B7.5–B7.6).

### Đóng góp cụ thể

- Hoàn thành toàn bộ Vòng 1:
  - Khối 1 ([Phiếu A](templates/form-a-criteria.md)): xác định mục tiêu cấp hệ thống, mục tiêu từ góc nhìn `NV-OANH` và `NV-HANH`, offline metric bước `file_carrier_fault`, telemetry production bên thứ ba, giải thích khoảng tin cậy 95%, hoàn thiện và ký niêm phong [acceptance_criteria.json](config/acceptance_criteria.json) **trước** lần đánh giá đầu tiên.
  - Khối 2A ([Phiếu B](templates/form-b-evaluation-gates.md) B0–B6): chạy baseline, phân tích lỗi `T-002@55`, lập bản đồ dữ liệu + ví dụ concept drift `REFUND-v4` (`2026-12-01`), HAZOP 5 guidewords trên `issue_refund` + 3 dòng ngoài kỹ thuật, checklist 9 nhóm có PIC cụ thể, pre-mortem 4 lăng kính.
  - Khối 2B ([guards.py](lab10/guards.py), [operating_gates.json](config/operating_gates.json), Phiếu B B7–B8): viết 4 cổng phòng ngừa (`pre_guard` ghim chính sách, `write_gate` cho `issue_refund`, `file_carrier_fault`, `notify_carrier`), kiểm thử 2 ticket hiểm `--adhoc` (`O-1002`, `O-1026`), viết runbook 1–3 & kịch bản giờ cao điểm, chốt cổng vòng 1 (`lab10.checkpoint`) và chốt quyết định v1 = `Tiếp tục`.
- Ghi chú sử dụng AI theo [RULES.md](RULES.md): có dùng trợ lý AI hỗ trợ đọc codebase, đề xuất cấu trúc các cổng phòng ngừa trong `lab10/guards.py` và rà soát trình bày Phiếu A, B; toàn bộ ngưỡng tiêu chí, con số vận hành và các lần chạy kiểm chứng đều tự thực thi và đối chiếu trực tiếp với `data/world.json` và output terminal.

### Bằng chứng

- Commit ký tiêu chí: `098a021` (`Sign acceptance criteria`, hash `66ce67a6a3e4830c47f670eb5b74be8d8b93eebbf1ba47ee5e94163e73048c3e`, `signed_at: 2026-11-18T21:06:24`).
- Commit chốt vòng 1: `87e2c4c` (`LAB 10: chốt cổng vòng 1, quyết định v1`, checkpoint hash `e003fd42`).
- Các lần chạy đánh giá trên bộ nền (`base`):
  - `R-base-before-20261118-212029-bde05c` (`base · base`: `pass_rate = 0.9909`, `pass_k = 0.9545`, hỏng `T-002@55`, hoàn sai `20000đ`, lỗi hãng oan `1`).
  - `R-base-after-20261118-212134-115baf` (`base · after`: `pass_rate = 1.0`, `pass_k = 1.0`, `0` hoàn sai, `0` lỗi oan, `0` PII, chi phí `4456đ`/ticket, `ROI = 1.24`, `0` ca ùn).
  - `R-base-prepared-20261118-212156-115baf` (`base · prepared`: tái lập toàn bộ `1.0`, qua `9/9` ngưỡng `lab10.gate`).
- Bộ test công khai `python -m unittest discover -s tests`: `Ran 13 tests ... OK`.
- Phiếu đã điền: `templates/form-a-criteria.md` (A1–A5), `templates/form-b-evaluation-gates.md` (B0–B8).

### Exit ticket

- **Một điều học được:** Phải ký niêm phong tiêu chí chấp nhận và dựng cổng phòng ngừa bằng hệ thống ngoài model (`write_gate` đối chiếu tracking DB, sổ cái trực tiếp, phê duyệt hợp lệ, lọc trường PII và `operating_gates.json`) thay vì tin vào prompt/LLM hay chạy số rồi mới chỉnh ngưỡng.
- **Một điều còn chưa chắc:** Trên bộ nền `base`, các ngưỡng hàng chờ và chi phí đang dựa trên dữ liệu giả định đều đặn `22` ticket/ca và `1` người trực (`6` ca/giờ); khi triển khai thật gặp mưa bão, giờ cao điểm dồn gấp 3 hoặc chuyển đổi chính sách `REFUND-v4` ngày `2026-12-01` (giảm `auto_limit_vnd` từ `200.000đ` xuống `100.000đ`), tỉ lệ chuyển duyệt và mức `reviewers_on_shift` thực tế cần đo lại ngay trong tuần đầu pilot.
