
function hideAvatar() {
    document.getElementById('avatar').style.visibility = "hidden";
}
function showAvatar() {
    document.getElementById('avatar').style.visibility = "visible";
}

function toggleQuestionList() {
    if (document.getElementById("question_list").style.display === "none") {
        document.getElementById("question_list").style.display = "block";
        document.getElementById("toggle_question_list_button").setAttribute("value", "Esconder lista de Questões");
    }
    else {
        document.getElementById("question_list").style.display = "none";
        document.getElementById("toggle_question_list_button").setAttribute("value", "Mostrar lista de Questões");
    }
}

function forbidenWords() {
    const words = ["abécula", "abentesma", "achavascado", "alimária", "andrajoso",
    "barregã", "biltre", "cacóstomo", "cuarra", "estólido", "estroso", "estultilóquio",
    "nefelibata", "néscio", "pechenga", "sevandija", "somítico", "tatibitate", "xexé", "cheché",
    "xexelento"];

    if (document.getElementById("comentario").value != null) {
        console.log(document.getElementById("comentario").value)
        const comment = document.getElementById("comentario").value.split(" ");

    for (const commentWord of comment) {
        for (const word of words) {
            console.log(commentWord + "-" +word)
            if (word == commentWord.trim().toLowerCase()) {
                commentIsNotValid();
                return;
            }
        }
    }
    commentIsValid();

    }

}

function commentIsValid() {
    if (document.getElementById("span_commentario") != null){
            document.getElementById("span_commentario").remove();
    }
    let span= document.createElement("span");
    span.setAttribute("id", "span_commentario");
    span.append(" Comentário válido")
    document.getElementById("comentario").after(span);
}

function commentIsNotValid() {
    if (document.getElementById("span_commentario") != null){
        document.getElementById("span_commentario").remove();
    }
    document.getElementById("comentario").value = "";
    document.getElementById("comentario").after("");
}