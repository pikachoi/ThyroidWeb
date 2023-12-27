
var password = document.getElementById("password1")
var confirm_password = document.getElementById("password2");

function validatePassword(){
    if(password.value != confirm_password.value) {
    confirm_password.setCustomValidity("비밀번호가 일치하지 않습니다.");
    } else {
    confirm_password.setCustomValidity(''); 
    }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;
