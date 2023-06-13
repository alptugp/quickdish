

function trackDeadClick(event) { 
    console.log("Enter trackDeadClick")
    const x = event.clientX;
    const y = event.clientY;

    var clickedElement = findClickedElement(x, y, event);
    console.log("is excluded element: " + isExcludedElement(clickedElement))
    console.log("clicked element: " + clickedElement)
    if (isExcludedElement(clickedElement) || clickedElement == null) { // Remove null check later
      console.log("Null check failed")
      return;
    }

    var tag_name =  clickedElement.tagName ? clickedElement.tagName.toLowerCase() : ''
    var class_name =  clickedElement.className ? clickedElement.className : ''
    var element_id =  clickedElement.id ? clickedElement.id : ''
  
    var data = {
      timestamp: new Date().toISOString(),
      url: window.location.href,
      x: x,
      y: y,
      tag_name: tag_name,
      class_name: class_name, 
      element_id: element_id
    };
  
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/drpapp/log-dead-click/', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify(data));
    console.log("Exit trackDeadClick")
}
  
function findClickedElement(x, y, event) {
    // var element = document.elementFromPoint(x, y);

    // while (element && element !== document.documentElement) {
    //   if (isClickableElement(element)) {

    //   }
    // }
  
    return event.target;
}
  
function isClickableElement(element) {
    return (
      element.tagName.toLowerCase() === 'a' &&
      element.href &&
      !element.getAttribute('target')
    );
}

/**
 * We don't want to track non-dead clicks, so we exclude the elements where if
 * a user clicks on them, they will be taken to a new page or perform some 
 * other action.
 */
function isExcludedElement(element) {
    return (
      element &&
      element.tagName &&
      element.tagName.toLowerCase() === 'a' &&
      element.href &&
      !element.getAttribute('target')
    );
    // element !== null &&
    // element !== undefined &&
    // element.tagName &&
    // element.tagName.toLowerCase() === 'button' ||
    // (element.tagName.toLowerCase() === 'a' && element.href) ||
    // (element.tagName.toLowerCase() === 'input' && element.type !== 'submit')

}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
  
document.addEventListener('click', trackDeadClick);
  