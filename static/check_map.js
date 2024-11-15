function loadCSVData() {
    const csvFilePath = '/static/predicted_cases_2024-01-01_UTF.csv';

    Papa.parse(csvFilePath, {
        download: true,
        header: true,  // 첫 번째 행을 열 제목으로 사용
        complete: function(results) {
            let data = results.data;

            // 빈 데이터 필터링 (구 이름 또는 감기 데이터가 비어 있는 항목 제거)
            data = data.filter(item => item.district && item.cold_case);

            // 데이터를 구 이름(district)을 기준으로 가나다순 정렬
            data.sort((a, b) => {
                if (a.district < b.district) return -1;
                if (a.district > b.district) return 1;
                return 0;
            });

            const tableBody = document.querySelector(".tableclass tbody");

            // 데이터를 한 행에 두 구의 정보를 표시하도록 처리
            for (let i = 0; i < data.length; i += 2) {
                const row = document.createElement("tr");

                // 첫 번째 구역 정보
                const district1 = document.createElement("td");
                district1.textContent = data[i].district; // 'district' 열에 구 이름 있음
                row.appendChild(district1);

                const cases1 = document.createElement("td");
                cases1.textContent = data[i].cold_case; // 'cold_case' 열에 감기 예측 수 있음
                row.appendChild(cases1);

                // 두 번째 구역 정보 (짝수 행에만 추가)
                if (i + 1 < data.length) {
                    const district2 = document.createElement("td");
                    district2.textContent = data[i + 1].district; // 두 번째 구의 이름
                    row.appendChild(district2);

                    const cases2 = document.createElement("td");
                    cases2.textContent = data[i + 1].cold_case; // 두 번째 구의 예측 감기 환자 수
                    row.appendChild(cases2);
                } else {
                    // 두 번째 구역 정보가 없는 경우 빈 셀 추가
                    row.appendChild(document.createElement("td"));
                    row.appendChild(document.createElement("td"));
                }

                // 행 추가
                tableBody.appendChild(row);
            }
        },
        error: function(error) {
            console.error("CSV 파일 로드 오류:", error);
        }
    });
}

document.addEventListener("DOMContentLoaded", loadCSVData);
