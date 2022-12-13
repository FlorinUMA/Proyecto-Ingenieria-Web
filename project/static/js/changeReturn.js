function custom_return(user) {
    logo = document.getElementById("logo");
    titulo = document.getElementById("titulo");

    logo.href = `/?user=${user}`;
    titulo.href = `/?user=${user}`;
}