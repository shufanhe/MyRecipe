let save_recipe = async function(title, category, content){
    const data = JSON.stringify({title : title, category: category, content: content});
    return fetch("/save_recipe", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        redirect: 'follow',
        body: data
    });
}