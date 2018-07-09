(function(jsonString) {
	var data = JSON.parse(jsonString);
	var value = data.occupancy;
	var output = "NULL";
	if (value) {
		output = "ON";
	} else if (!value) {
		output = "OFF";
	}
	return output;
})(input)
