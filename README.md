# Label Fresh

## CS 304 FA19 semester project

[Wellesley Fresh](http://www.wellesleyfresh.com/index.html) is really, really bad at labeling the food it serves. Labels are often missing, confusing, or incorrect. 
    
As someone with celiac disease, an autoimmune disorder which requires me to eat a gluten-free diet, I often have to decide whether I want to trust the labels at the dining halls or take the chance of getting sick, and the inconsistencies of the online menu mean that I can’t tell if a dining hall will have food for me before I get there. 
> (Note that none of this is the fault of the chefs and dining hall workers. This is a management issue only.) 

Label Fresh is a database-backed website that allows the community to report labelling errors as they are encountered, giving people with dietary restrictions more information with which they can base their decisions of where to eat.

I would like to have integration with the online menu, but it is run entirely in JavaScript, making it hard to get data from.

### Checklist:
* Draft
  - [x] Homepage -- uses base HTML template that all other pages will extend
  - [x] Web form to insert new food label report into the database
  - [x] Web page to view individual existing entries in the database
  - [x] Search function by food name
  - [x] Redirects to list of links to individual results
  - [x] Ability to update existing entries
  - [x] Ability to narrow search by dining hall
  - [x] Ability to delete existing entries
  - [x] Ability to upload images
* Alpha version
  - [x] Chronological view of entries
  - [x] With Ajax
  - [x] Wellesley login
  - [x] Ownership check for deletion and update
* Beta version
  - [x] Make it look (sort of) pretty (I tried, CSS is not my strong suit)
