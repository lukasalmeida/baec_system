const nameInput =
    document.getElementById("name");

const rankInput =
    document.getElementById("rank");

const passportInput =
    document.getElementById("passport");

const ageInput =
    document.getElementById("age");

const dateInput =
    document.getElementById("date");

const previewName =
    document.getElementById("preview-name");

const previewRank =
    document.getElementById("preview-rank");

const previewPassport =
    document.getElementById("preview-passport");

const previewAge =
    document.getElementById("preview-age");

const previewDate =
    document.getElementById("preview-date");

nameInput.addEventListener(
    "input",
    () => {

        previewName.innerText =
            nameInput.value || "NOME AQUI";

    }
);

rankInput.addEventListener(
    "change",
    () => {

        previewRank.innerText =
            rankInput.value || "PATENTE AQUI";

    }
);

passportInput.addEventListener(
    "input",
    () => {

        previewPassport.innerText =
            passportInput.value || "Nº AQUI";

    }
);

ageInput.addEventListener(
    "input",
    () => {

        previewAge.innerText =
            ageInput.value || "IDADE AQUI";

    }
);

dateInput.addEventListener(
    "input",
    () => {

        previewDate.innerText =
            formatDate(dateInput.value);

    }
);