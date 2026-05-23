function formatDate(dateString){
    if(!dateString){
        return "DATA AQUI";
    }

    const date = new Date(dateString);

    return date.toLocaleDateString(
        "pt-BR"
    );

}