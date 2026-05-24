const form = document.getElementById("certificate-form");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const formData = new FormData(form);

    try {

        const response = await fetch("/api/breve", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        console.log(data);

        const mockup = document.querySelector(".mockup-wrapper");

        const canvas = await html2canvas(mockup, {

            useCORS: true,

            scale: 3

        });

        const image = canvas.toDataURL("image/png");

        const link = document.createElement("a");

        link.href = image;

        link.download = "breve-baec.png";

        link.click();


    } catch (error) {

        console.error(error);

        alert("Erro ao salvar.");

    }

});