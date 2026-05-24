const campoNome = document.getElementById("name");
const campoPatente = document.getElementById("rank");
const campoPassaporte = document.getElementById("passport");
const campoIdade = document.getElementById("age");
const campoData = document.getElementById("date");

const visualizacaoNome = document.getElementById("preview-name");
const visualizacaoPatente = document.getElementById("preview-rank");
const visualizacaoPassaporte = document.getElementById("preview-passport");
const visualizacaoIdade = document.getElementById("preview-age");
const visualizacaoData = document.getElementById("preview-date");

campoNome.addEventListener("input", () => {
    visualizacaoNome.innerText = campoNome.value || "NOME AQUI";
});

campoPatente.addEventListener("change", () => {
    visualizacaoPatente.innerText = campoPatente.value || "PATENTE AQUI";
});

campoPassaporte.addEventListener("input", () => {
    visualizacaoPassaporte.innerText = campoPassaporte.value || "Nº AQUI";
});

campoIdade.addEventListener("input", () => {
    visualizacaoIdade.innerText = campoIdade.value || "IDADE AQUI";
});

campoData.addEventListener("input", () => {
    visualizacaoData.innerText = formatarData(campoData.value);
});

const campoFoto = document.getElementById("photo");
const visualizacaoFoto = document.getElementById("preview-photo");

campoFoto.addEventListener("change", () => {
    const arquivo = campoFoto.files[0];

    if (arquivo) {
        const leitor = new FileReader();

        leitor.onload = (evento) => {
            visualizacaoFoto.src = evento.target.result;
        };

        leitor.readAsDataURL(arquivo);
    }
});
