const form = document.getElementById("certificate-form");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const formData = new FormData(form);

    try {

        const response = await fetch("api/breve", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        console.log(data);

        alert("Brevê salvo com sucesso!");

    } catch (error) {

        console.error(error);

        alert("Erro ao salvar.");

    }

});