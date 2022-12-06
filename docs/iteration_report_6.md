# Food Recipe Project Iteration Report 6

Tasks Assigned
----------------
1. Shufan:
   - Incorporate a separate table for ingredients in the database 
   - Front-end for view recipe
   - Unit tests for edit/delete reviews, and notifications.
   - Upload/set recipes of the day through admin account.
2. Khanh:
   - Upload images for recipes
   - Allow users to change their profile pictures, name and emails.
   - Allow other users to follow each other accounts so that they can know when a user create a new recipe
   - Check edge-cases to make more comprehensive unit-tests.
3. Diana:
   - Finish implementing user preferences.
   - Restrict creator to only select from the given categories when they create a recipe.
   - Front-end for pages.
   - Add more unit-tests.

Completed Work
----------------
1. Shufan:
   - Front-end for view recipe: changed the location and font of several things, changed word buttons to icon buttons, added accordion for reviews
   - Unit tests for edit/delete reviews
   - Improved notifications: Users can click on embedded links to see the profile of the person that liked/reviewed their post and the post itself. If a post is deleted and the user tries to click on it, user is redirected back to notifications and flashed a warning message. Changed format of datetime, got rid of the decimals and seconds and seperated date and time into two attributes.
   - Fixed homepage slideshow cover
2. Khanh:
   - Worked on frontend for user account page
   - Implemented following other users, the following list will be shown in the user account

3. Diana:  
   - Updated format of cards. It used to show all of the recipe on the card, now only shows the title. This is neater so user can see the cards better as it was recommended after testing day.

Still Needs Completion
----------------
1. Shufan:
   - Incorporate a separate table for ingredients in the database 
   - Unit tests for edit/delete reviews, and notifications.
2. Khanh:
   - More comprehensive unit tests where it tests the functionality of forms, buttons and actions instead of just verifying what shows up on the webpage
   - Allow users to change their profile pictures, name and emails
   - Update profile is currently a button and needs to be implemented
   - Need to design the webpage more so it looks better when changing screens
   - Let user upload images to the recipe and more interactive when creating recipe 
3. Diana: 
   - Tags need to be completed, figured out a way to get the input from the user. Need to work on getting the recipes to show up with the respective diet tag. Once, I am able to implement this, I think categories will be implemented similarly and get that done. Cards on categories are still not aligning as they should, working on being able to align them.

Troubles/Issues/Roadblocks
----------------
1. Shufan - Figuring out dependencies among tables, for example if a recipe is deleted what happens to the notification related to it, and where will people be redirected to if they try to click on a recipe that is deleted (notification about the recipe remains even if recipe itself is deleted, people will get a warning message saying that the recipe has been deleted)
2. Diana - Schema/database, working with queries for tags was a little challenging since I do not have enough experience.
3. Khanh - Saving images is having a problem of whether saving locally or in database, this will be put in next week when I research more


Adjustments to Overall Design
----------------
1. We are going to add recipes to slideshow and recipe of the day work on homepage before the presentation because they would get deleted when we reinitialize the database.


Helpful Tools & Approaches
----------------
1. Stackoverflow.
2. Bootstrap documentation.
3. Shufan - inspecting frontend code for other websites

One Important Thing Learned
----------------
1. Shufan learned how to use icons with for post methods (inside a button, and use a form to specify the method as 'post')
2. Diana learned to trust herself
3. Khanh learned how to plan a project as well as add user stories, how tests should be done and cover what of the application and how to host application on different website. Also, how to use JavaScript efficiently


Week 7 and 8
----------------
Tasks:
1. Shufan:
   - Update homepage layout so it is responsive in different sizes of screen.
   - Tasks that still need completion from last week.
   - Add alt text for everything, make sure things are accessible.

2. Khanh:
   - Improve uploading image in post recipe.
   - Improving search recipe so it does not show all results at once
   - User profile and creating recipe websites need to change their layouts so user can interact when posting recipe

3. Diana
   - Finish tasks from last week. 

