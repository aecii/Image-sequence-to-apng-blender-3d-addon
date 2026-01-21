Blender 3d addon: 
Image sequence to *.apng (animated PNG)
@aecii_3d

This is an addon that will take an image sequence and convert it to animated *.apng. 
The benefit of APNG is that you are not limited to just 256 colors of an animated gif. 
Useful if you want to make higher quality animated images and elements for your 
obs streams. *.apng is supported by OBS studio.



How to install this addon into blender: 
1) Edit -> prefs -> Add-ons. 
2) Go to the top left chevron and drop it down to install add-on from disk. (like every other add on you install) 
3) After that, Make sure it's enabled. 
No need to restart blender.


How to use in blender: 
In blender, look at the properties panel (lower right side of blender) and go to the output tab (printer icon) 
Scroll all the way down until you see "APNG Export"

1) Tell it where your image sequence is. 
2) Tell it wheere to send the output. 
3) Set your FPS, and and then click the EXPORT button. 
Done. 



You can use Irfanview or any other worthy image viewer to check the file. Now you have an *.apng file saved. Take that file into OBS. For it to work in OBS you need to import it as a Media Source and select "browse all files" to see it. 
Also, Be sure to check "Loop" if its supposed to loop.


Addon Details: 
Uses pure python. Made for Blender 4.5.5 LTS. 
(Feel free to test on older versions and let me know if it works.)

License MIT. 
Do not resell. Do not reupload please. 
Monetary tips appreciated but not required. 
Thank you and go make something nice.




-----------Change log -------------

4:16 PM 1/21/2026 --- V1.0 initial release. 

