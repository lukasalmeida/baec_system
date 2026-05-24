const downloadBtn =
    document.getElementById(
        "download-btn"
    );

downloadBtn.addEventListener(
    "click",
    async () => {

        const payload = {
            nome:
            document
                .getElementById("name")
                .value,

            patente:
            document
                .getElementById("rank")
                .value,

            passaporte:
            document
                .getElementById("passport")
                .value,

            idade:
            document
                .getElementById("age")
                .value,

            data_conclusao:
            document
                .getElementById("date")
                .value

        };

        const response =
            await fetch(
                "/api/breve",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )

                }
            );

        const result =
            await response.json();

        console.log(result);

        alert(
            "Brevê salvo com sucesso!"
        );

    }
);