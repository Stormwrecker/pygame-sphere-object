# Pygame Sphere Object

The follow program creates a sphere-looking object using Pygame-CE. How it really works is that it takes an image,
slices it into 1 x 'your-height' segments and places them onto a circular track. Each segment is sorted according to z depth
for blitting. Manipulating `Sphere.master_angle` will move the slices up and down the track and give the illusion of a
3D spherical object.

I've added a stretch effect just to add a more natural feel to the object's movement. To create an image for the
`Sphere`, simply figure out your height (say 16px), multiply that by π (say ~51px), and that will be sufficient for
'wrapping' around the whole object.

Hopefully, it's generic enough for you to be able to use it somewhere in your own projects.
Have fun experimenting with this technique, but please give credit if used!

Simply use this line in your docs: `Sphere Code by Stormwrecker`

A not-amazing screenshot of the Sphere object in action:

<img width="798" height="479" alt="image" src="https://github.com/user-attachments/assets/b3867616-147a-41c5-bb7d-989070a3c5c3" />


## Notes

When blitting an object, make sure that you blit to `display` and NOT `screen`. The `display` is the actual canvas that
everything gets drawn on. Then the display is scaled to fit the window, perfect for pixel artists.

Using Pygame (not -CE) will result in your sphere object having a red background as I set color-key to red for the image.

I currently added where if you press a key, the Sphere object resets position. You will also notice in the `.update()` and `.draw()` methods, there's
some extra code for some non-necessary physics. You can mess around with the values there or remove it entirely.
