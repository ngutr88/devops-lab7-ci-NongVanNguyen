# Lab 7 — Jenkins, Nexus & SonarQube

Sinh viên: **Nông Văn Nguyên — DTC235180138**.

Nguồn bài thực hành: [Lab7_HuongDan.md](https://github.com/PhamThuongBlog/VHBTPM_DevOps_2026/blob/main/Labs/B%C3%A0i%207/Lab7_HuongDan.md).

## Cấu trúc

- `docker-compose.yml`: ba dịch vụ và các volume dữ liệu.
- `sample-java-app`: Java 17, Maven, Calculator và 6 JUnit 5 tests.
- `Jenkinsfile`: bản pipeline ở gốc để nộp bài.
- `sample-java-app/Jenkinsfile`: bản Jenkins Job đọc từ SCM, cùng nội dung với bản gốc.
- `config/maven-settings-nexus.xml`: mẫu Maven settings đọc credentials từ biến môi trường.
- `scripts`: cấu hình môi trường lab mới qua CLI/API.
- `evidence`, `screenshots`: minh chứng thực thi trên máy, không đưa log lên GitHub.
- `.private`: thông tin đăng nhập sinh tự động, được Git bỏ qua; không đưa vào ZIP nộp bài.

## Build tại máy

Cần JDK 17+ và Maven 3.9.x:

```powershell
mvn -B -f sample-java-app/pom.xml clean package
```

Nếu dùng Maven đã tải riêng cho bài này:

```powershell
& .\.tools\apache-maven-3.9.9\bin\mvn.cmd -B -f sample-java-app/pom.xml clean package
```

Artifact: `sample-java-app/target/ci-demo-1.0.0-SNAPSHOT.jar`.

## Dịch vụ và Jenkins Job

```powershell
docker compose up -d
docker compose ps
```

| Dịch vụ | Địa chỉ |
|---|---|
| Jenkins | http://localhost:8080 |
| Nexus | http://localhost:8081 |
| SonarQube | http://localhost:9000 |

Job: `DevOps-Lab7-CI-Pipeline`; Git repository: `https://github.com/ngutr88/devops-lab7-ci-NongVanNguyen.git`; branch `main`; script path `sample-java-app/Jenkinsfile`.

Các stage: Checkout → Build → Test → SonarQube Analysis → Package → Publish to Nexus.

Jenkins dùng Maven tool `M3`, SonarQube server `SonarQube`, credentials `github-credentials`, `sonarqube-token`, `nexus-credentials` và managed file `maven-settings-nexus`. Mật khẩu dịch vụ được sinh ngẫu nhiên và lưu trong `.private/services.json` trên máy thực hành.

Pipeline dùng Poll SCM `H/5 * * * *`, phương án thay thế webhook được bài hướng dẫn cho phép. Jenkins kiểm tra thay đổi khoảng mỗi 5 phút; chỉ build khi SCM có thay đổi. Chưa mở Jenkins ra Internet và chưa cấu hình GitHub webhook.

Script `scripts/finish-setup.ps1` dành cho lần cấu hình đầu tiên của môi trường lab mới, sau khi Maven đã nằm trong `.tools/apache-maven-3.9.9`. Script sử dụng phiên GitHub hiện tại của Git Credential Manager, chỉ cấu hình repository bài lab. Không chạy lại script này để ghi đè credentials của môi trường đã cấu hình.

## Kiểm tra kết quả

1. Jenkins → Job → build → Console Output, Test Result, Artifacts.
2. Nexus → Browse → `maven-snapshots` → `com/devops/lab7/ci-demo/1.0.0-SNAPSHOT`.
3. SonarQube → project `devops-lab7`.

Tên artifact snapshot trong Nexus có timestamp; không phải đường dẫn bản release `1.0.0`.

## Dọn dẹp và chạy lại

```powershell
docker compose down
docker compose up -d
```

`down` giữ dữ liệu Jenkins/Nexus/SonarQube và Maven trong volume. Chỉ dùng `docker compose down -v` khi chủ động muốn xóa toàn bộ dữ liệu bài lab.

## Điều chỉnh so với mẫu

- Chỉ mở cổng trên localhost.
- Bỏ Docker socket mount vì pipeline Java này không build Docker image.
- Thu thập JUnit ở `post always` để giữ cả kết quả test lỗi.
- Tắt checkout mặc định để không checkout hai lần.
- Không cho hai build chạy đồng thời trên cùng job.
- Dùng mật khẩu ngẫu nhiên và Jenkins Credentials thay vì mật khẩu ví dụ trong tài liệu.
- Dùng repository `maven-snapshots` có sẵn của Nexus khi tồn tại.
