/**
 * Transform the input RGB color (in the format "R,G,B" such as "0,0,125") into a JSON string
 * acceptable by the IKEA light bulb.
 */
(function(i) {
var rgb = input.split(',');

var payload = {};
payload.color = {};
payload.color.r = parseInt(rgb[0]);
payload.color.g = parseInt(rgb[1]);
payload.color.b = parseInt(rgb[2]);

return JSON.stringify(payload);

})(input)
