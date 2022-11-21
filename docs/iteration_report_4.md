# Food Recipe Project Iteration Report 4

Tasks Assigned
----------------
1. Shufan:
   - Finish like/review recipes
   - Front-end for homepage
2. Khanh:
   - Save recipes - for viewers to be able to save favorite recipes.
   - Front-end user account - same thing as for homepage, make it user accessible.
3. Diana:
   - Delete/edit recipes - only for creators to be able to delete and review their recipes.
   - Implement user preferences - allow users to only view recipes that work with their dietary restrictions.
   - Front-end categories - specifically focused on categories

Completed Work
----------------
1. Shufan:
   - Like Recipe: Changing between like and unlike, incrementing and decrementing like counts. Redirecting is still not working, needs to work on js
   - Review Recipe - allowing users to leave a review on recipe after cooking it.
   - New Navbar design
   - Debugging past code - specifically post_recipe (recipes show up on user account after posting it), and view_recipe (made it work for user account and categories)
2. Khanh:
   -  Save recipe
   -  Added verification for registration and reset password - you get a code to verify your account.
   -  Front-end for user account.
   -  Updated redirect to better html page rather than give 401 page.
3. Diana:
   - Delete recipe.
   - Edit recipe.
   - Added warning message for users trying to post without logging in instead of showing an error.
   - Updated categories so user can now see list of recipes in each category.

Still Needs Completion
----------------
1. Shufan:
   - Fix redirecting for like and review recipe - still needs help with JavaScript to complete.
   - Unit-tests: view recipe, like recipe
2. Khanh:
   - Frontend for user account page - make it user accessible.
3. Diana:
   - Implement user preferences - spoke with Evan and got an idea on how, basically give the creator options to select what the recipe is. For example if it is vegan they will select that option. Then when the user updates their account they will get the option to exclude recipes that go against their dietary restrictions.
   - Front-end categories - specifically focusing on page that lists recipes after clicking a specific category.

Troubles/Issues/Roadblocks
----------------
1. Unittests for verification when registering and reseting password.
2. JavaScript for like.

Adjustments to Overall Design
----------------
1. Changed structure.
   - Deleted backend folder.
   - Put app.py in main directory.
   - Put all html file in one folder that is in the main directory.
   - Database is in main directory, deleted second database that was made.

Helpful Tools & Approaches
----------------
1. Stackoverflow.
2. TA Evan.
3. Mark's office hours.
4. Reviewing flaskr assignment.

One Important Thing Learned
----------------
1. Make better use of the debugger.
2. That we need unittests.
3. Count everything you did during the week, not just user stories
4. Be very detailed with everything.

Week 5
----------------
Tasks:
1. User Stories:
   - Notifications for creators to see their likes and reviews after a viewer leaves them a like or review.
   - Creator profiles, allowing other users to see profiles.
   - Make sure to add unit-tests for stories!

Assigning:
1. Shufan:
   - Notifications for creators
   - Front-end for homepage.
2. Khanh:
   - Creator profiles, allowing other users to see profiles.
   - Front-end user account
3. Diana:
   - Implement user preferences
   - Finish up front end for categories

Week 6
----------------
1. Finish off front-end for all pages users will see.
2. Unit-tests
3. Refine anything that is left over.

Week 7
----------------
1. Profile pictures
2. Refine front-end for any pages that still need it.
3. Put in example recipes.
