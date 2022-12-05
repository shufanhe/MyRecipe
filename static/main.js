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

const image_input = document.querySelector("#image-input");

image_input.addEventListener("change", function() {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    const uploaded_image = reader.result;
    document.querySelector("#display-image").style.backgroundImage = `url(${uploaded_image})`;
  });
  reader.readAsDataURL(this.files[0]);
});

let save_recipe = async function(title, category, content){
    const data = JSON.stringify({title : title, category: category, content: content});
    return fetch("/save_recipe", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        redirect: 'follow',
        body: data
    });
}

