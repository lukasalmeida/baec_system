const formulario = document.getElementById("certificate-form");

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const dadosFormulario = new FormData(formulario);

    try {
        const resposta = await fetch("/api/breve", {
            method: "POST",
            body: dadosFormulario,
        });

        const dadosResposta = await resposta.json();
        console.log(dadosResposta);

        const areaMockup = document.querySelector(".mockup-wrapper");
        const telaRenderizada = await html2canvas(areaMockup, {
            useCORS: true,
            scale: 3,
        });

        const imagem = telaRenderizada.toDataURL("image/png");
        const linkDownload = document.createElement("a");

        linkDownload.href = imagem;
        linkDownload.download = "breve-baec.png";
        linkDownload.click();
    } catch (erro) {
        console.error(erro);
        alert("Erro ao salvar.");
    }
});
