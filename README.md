# CanvasToNotion
**Notion**
* Course names are automatically created in multi select
* Must sort Notion DB table view by Date, Decending to avoid pagation issues
* Stops updating due dates after completed
* Stops updating assignments with due date 1 days ago or if no due date, created 60 days ago  
<br>

**To do**
* after initial data pull from canvas, only pull new info
* try except function for if api calls fail
* don't run overnight?
* simplify notion key thingy
* make all day if time is 11:59pm PACIFIC TIME
* if time is xx:05 add 0