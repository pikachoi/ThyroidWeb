
const text_modal1 = document.querySelector('.text_modal1');
const text_modal2 = document.querySelector('.text_modal2');
const text_modal3 = document.querySelector('.text_modal3');

var comment_modal_close1 = document.getElementsByClassName("comment_close_button1")[0];
var comment_modal_close2 = document.getElementsByClassName("comment_close_button2")[0];
var comment_modal_close3 = document.getElementsByClassName("comment_close_button3")[0];



const btn_like1 = document.querySelector('.like');
const btn_dislike1 = document.querySelector('.dislike');
const btn_like2 = document.querySelector('.like1');
const btn_dislike2 = document.querySelector('.dislike1');
const btn_like3 = document.querySelector('.like2');
const btn_dislike3 = document.querySelector('.dislike2');


btn_like1.addEventListener('click', () => {
    text_modal1.style.display = 'block';

comment_modal_close1.onclick = function() {
    text_modal1.style.display = "none";
}
});
btn_dislike1.addEventListener('click', () => {
    text_modal1.style.display = 'block';

comment_modal_close1.onclick = function() {
    text_modal1.style.display = "none";
}
});
btn_like2.addEventListener('click', () => {
    text_modal2.style.display = 'block';


comment_modal_close2.onclick = function() {
    text_modal2.style.display = "none";
}
});
btn_dislike2.addEventListener('click', () => {
    text_modal2.style.display = 'block';


comment_modal_close2.onclick = function() {
    text_modal2.style.display = "none";
}
});

btn_like3.addEventListener('click', () => {
    text_modal3.style.display = 'block';


comment_modal_close3.onclick = function() {
    text_modal3.style.display = "none";
}
});

btn_dislike3.addEventListener('click', () => {
    text_modal3.style.display = 'block';

comment_modal_close3.onclick = function() {
    text_modal3.style.display = "none";
}
});




