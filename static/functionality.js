let save_recipe = async function(title, category, content){
    const data = {title : title, category: category, content: content};
    return fetch("/save", {
        method: 'POST',
        headers: {
      'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: JSON.stringify(data)
    });
}
let deleted_rows = (function(i){
    const lists = document.getElementById(i);
    lists.remove();
})