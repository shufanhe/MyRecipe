function like_recipe(recipe_id){
    const data = {like_me : recipe_id };
    return fetch("/like_recipe",
                {method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    redirect: 'follow',
                    body: JSON.stringify(data)});
};


function setupEvents() {
  const like_button = document.querySelector("#like_button");
  like_button.addEventListener('click', like_recipe());
  like_button.addEventListener('click', () => {like_button.classList.toggle('liked')});
};


document.addEventListener('DOMContentLoaded', setupEvents);



