	function OtherRectangle(xmin,xmax,ymin,ymax,colorline,fillcolor){
	var rectangle ={'type': 'rect','x0': xmin,'y0': ymin,'x1': xmax,'y1': ymax,'line': {'color': colorline,'width': 1},'fillcolor': fillcolor};
	return rectangle;
	}


	function bargridRectangle(x,y,xstep,ystep,colorline,fillcolor){
	var rectangle ={'type': 'rect','x0': x[0]-xstep,'y0': y[0]-ystep,'x1': x[1]+xstep,'y1': y[1]+ystep,'line': {'color': colorline,'width': 1},'fillcolor': fillcolor};
	return rectangle;
	}

