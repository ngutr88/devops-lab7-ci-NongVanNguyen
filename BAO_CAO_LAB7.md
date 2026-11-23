# Báo cáo thực hành Lab 7

**Sinh viên:** Nông Văn Nguyên  
**MSSV:** DTC235180138

## Mục tiêu đã thực hiện

- Dựng Jenkins, Nexus Repository và SonarQube bằng Docker Compose.
- Tạo ứng dụng Maven Java 17 có lớp `Calculator` và 6 kiểm thử JUnit 5.
- Cấu hình Jenkins Pipeline Job đọc `sample-java-app/Jenkinsfile` từ GitHub.
- Chạy 6 stage: Checkout, Build, Test, SonarQube Analysis, Package, Publish to Nexus.
- Lưu `.jar` trong Jenkins và publish snapshot lên `maven-snapshots` của Nexus.

## Kết quả xác minh

| Hạng mục | Kết quả |
|---|---|
| Docker stack | `lab7-jenkins`, `lab7-nexus`, `lab7-sonarqube` đang chạy |
| Maven local | `BUILD SUCCESS` |
| Unit test | 6 tests, 0 failures, 0 errors |
| Jenkins | Build `#4`: `SUCCESS` |
| Artifact Jenkins | `ci-demo-1.0.0-SNAPSHOT.jar` |
| Nexus | `ci-demo-1.0.0-20261123.032534-1.jar` trong `maven-snapshots` |
| SonarQube | Project `devops-lab7`; 0 bugs, 0 vulnerabilities, 0 code smells |

**Xác nhận:** Pipeline Jenkins build `#4` là lần chạy nộp bài thành công đầy đủ các stage.

## Link và cấu hình

- GitHub: `https://github.com/ngutr88/devops-lab7-ci-demo`
- Jenkins: `http://localhost:8080`
- Nexus: `http://localhost:8081`
- SonarQube: `http://localhost:9000`
- Jenkins Job: `DevOps-Lab7-CI-Pipeline`
- SCM branch: `main`
- Script path: `sample-java-app/Jenkinsfile`
- Auto trigger: Poll SCM `H/5 * * * *`

## Minh chứng

Xem thư mục `screenshots/` và `evidence/`. File `pipeline-build-4.log` ghi nhận tất cả stage thành công và upload artifact lên Nexus.

## Lưu ý triển khai

Nexus Community Edition yêu cầu chấp nhận EULA qua REST API trước khi upload/download component. Script `scripts/configure-services.py` đã thực hiện thao tác này trong lần cấu hình đầu tiên. Secrets được lưu cục bộ tại `.private/`, đã loại khỏi Git và gói nộp.
