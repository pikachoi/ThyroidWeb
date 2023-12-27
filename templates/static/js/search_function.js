function searchClear() {
    const url = new URL(window.location.href);
    url.searchParams.delete('keyword');
    url.searchParams.delete('search');
    url.searchParams.delete('entry');

    window.location.href = url.href;
}

function dont_delete() {
    alert("이미지를 업로드 한 진단의만 삭제할 수 있습니다.")
}

function confirmDelete(button){
    if (confirm("정말 삭제하시겠습니까?")) {
        button.closest("form").submit();
    }

}



function submitForm() {
    var form = document.getElementById("count_form");
    form.action = "{% url 'patient_list' %}?keyword={{ keyword }}&search={{ search_query }}";
    form.submit();
}