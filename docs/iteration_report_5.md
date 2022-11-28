# Food Recipe Project Iteration Report 5

Tasks Assigned
----------------
1. Shufan:
   - Notifications for Creators
   - Front-end for homepage
   - Allowing users to edit and delete their reviews
2. Khanh:
   - Allowing users to see each others' profiles.
   - Front-end for user account
   - Warning message to tell users they need an account in order to post/like etc. (instead of giving 401 page).
3. Diana:
   - Implement user preferences: users can enter allergies and dietary restrictions so that the posts that contain those ingredients will not show up when the user searches for recipes.
   - Finish up front end for categories

Completed Work
----------------
1. Shufan:
   - Front-end for homepage: Changed buttons to icons on the navbar, slideshow, redisigned recipe of the day, added footer
   - Edit and Delete reviews in view_recipe
   - Notifications for users when someone likes/reviews their recipe
2. Khanh:
   -  Allowing users to see eachothers' profile. When the user see the recipe, they can see who created it and go to that person's profile
   -  Made changes to verification process for registration so that users can no longer login when their accounts is not verified
   -  When users forget to verify their accounts, they can register again to verify their account
   -  Made changes so that the author of the recipe cannot save their own recipes
3. Diana:
   - No tasks completed, still in progress.

Still Needs Completion
----------------
1. Shufan:
   - Refine creator notifications: red dot on icon should only show up if there is unread notifications; Make sure users can view the accont of the user who liked/reviewed their recipe by clicking on the user name and view the recipe by clicking on the image, after those tasks are done.
   - Unit tests for edit/delete reviews, and notifications.
2. Khanh:
   - Frontend for user account page - make it user accessible and friendly. Will add a profile picture so that the user can upload their own. 
   - Some buttons need to work without reloading the pages
   - unit tests, more coverage than now as currently unit tests are only testing the basic of the page made from the right template
3. Diana:
   - Implement user preferences - decided to go with the tag route. Having issues with the schema and how to structure it in the database. I will go to office hours this week to get help with this.
   - Front-end for categories page - having issues with how to format the recipes since we are using a for loop to add them.

Troubles/Issues/Roadblocks
----------------
1. Had some troubles with bootstrap, formating the cards that we are using for recipes. Formating things in the correct position. Sizing of pictures and icons.
2. Diana - Schema/database. Adding tags is something new to me specifically adding it to our database and joining things together. I need to get extra help to work on this.
3. Shufan tried to work on uploading image for recipes but didn't end up working, did not have enough time so prioritized the assigned tasks.

Adjustments to Overall Design
----------------
1. No adjustment.

Helpful Tools & Approaches
----------------
1. Stackoverflow.
2. Bootstrap documentation.
3. Reddit.

One Important Thing Learned
----------------
1. Look at original documentation before searching for example code, provides better solutions and might save some time.
2. Be very detailed with everything.
3. Be careful to not lose code when merging things.
4. Ask for help.

Week 6
----------------
Tasks:
1. User Stories:
   - Incorporate a seperate table for ingredients in the database 
   - Restrict creator to only select from the given categories when they create a recipe.
   - Upload images for recipes
   - Finish off front-end for all pages.
   - Finish/ refine unit-tests to check edgecases.
Assigning:
1. Shufan:
   - Incorporate a seperate table for ingredients in the database 
   - Front-end for view recipe
   - Unit tests for edit/delete reviews, and notifications.
   - Upload/set recipes of the day through admin account.
   - Keep trying to implement JavaScript for like/review
2. Khanh:
   - Upload images for recipes
   - Allow users to change their profile pictures, name as well as emails
   - Allow other users to follow each other accounts so that they can know when a user create a new recipe
   - More concrete and coverage for unit tests
3. Diana:
   - Finish implementing user preferences.
   - Restrict creator to only select from the given categories when they create a recipe.

