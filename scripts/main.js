let like_page = async function(id){
    const data = {to_like : id};
    return fetch("/like_recipe", {
        method: 'POST',
        headers: {
      'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: JSON.stringify(data)
    });
}
let like_recipe = (function(i){
    const lists = document.getElementById(i);
    lists.remove();
})

const button = document.querySelector('.btn')
button.addEventListener('click', () => {
    button.classList.toggle('liked')
})
