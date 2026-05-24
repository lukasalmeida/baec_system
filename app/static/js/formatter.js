function formatarData(textoData) {
    if (!textoData) {
        return "DATA AQUI";
    }

    const data = new Date(textoData);

    return data.toLocaleDateString("pt-BR");
}
