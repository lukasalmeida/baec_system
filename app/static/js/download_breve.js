const botaoDownload = document.getElementById("download-btn");

if (botaoDownload) {
    botaoDownload.addEventListener("click", async () => {
        try {
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
            alert("Erro ao gerar download.");
        }
    });
}
