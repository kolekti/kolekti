$(function() {
    var svg = d3.select(window.document.body).select('div')
    var svglist = window.document.getElementsByTagName('div')

    window.drawchart(svglist[0], false, 725);
//    stdout.write(svg.html())
});
