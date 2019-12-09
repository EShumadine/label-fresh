/** 
 * Takes in a list of the next reports to show, and modifies the DOM to
 * add them.
*/
function showmore(info) {
    var reports = info['reports'];
    var nextDate = info['nextDate'];
    for (var index in reports) {
        date = Object.keys(reports[index])[0];

        // create full elements to add for date
        var dateList = document.createElement('li');
        var dateHead = document.createElement('h2');
        dateHead.innerHTML = date;
        var itemList = document.createElement('ul');
        itemList.setAttribute('class', 'items');
        dateList.appendChild(dateHead);
        dateList.appendChild(itemList);

        for (var item in reports[index][date]) {
            item = reports[index][date][item];

            // create the full elements to add for report
            var listItem = document.createElement('li');
            var table = document.createElement('table');
            var div = document.createElement('div');
            div.setAttribute('class', 'calendar-item');
            var headText = document.createElement('h3');
            var link = document.createElement('a');
            link.setAttribute('href', item['url']);
            link.innerHTML = item['name'];
            var row1 = document.createElement('tr');
            var hallHead = document.createElement('th');
            hallHead.innerHTML = 'Dining Hall';
            var mealHead = document.createElement('th');
            mealHead.innerHTML = 'Meal';
            var row2 = document.createElement('tr');
            var hall = document.createElement('td');
            hall.innerHTML = item['hall'];
            var meal = document.createElement('td');
            meal.innerHTML = item['meal'];

            // connect into structure
            itemList.appendChild(listItem);
            listItem.appendChild(div);
            div.appendChild(headText);
            headText.appendChild(link);
            div.appendChild(table);
            table.appendChild(row1);
            row1.appendChild(hallHead);
            row1.appendChild(mealHead);
            table.appendChild(row2);
            row2.appendChild(hall);
            row2.appendChild(meal);
        }
        // add to DOM
        $("#dates").append(dateList);
    }

    if (nextDate != null) {
        // set next date
        $("#next-date").val(nextDate);
    } else {
        // remove button to show more
        $("#showMore").remove();
    }
}

$("#showMore").submit(function(e) {
    if (progressive_on) {
        e.preventDefault();
        var nextDate = $(this).closest("form").find("#next-date").val();
        console.log(nextDate);
        $.post(AjaxURL, {'next-date': nextDate}, showmore);
    }
});