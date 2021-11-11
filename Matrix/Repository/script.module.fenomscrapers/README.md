

# Welcome to the *Fenom Scrapers* Project




## Fenomscrapers Repo

You can add the source directory to your own repository for convenience and updates
```
<dir>
    <info compressed="false">https://raw.githubusercontent.com/mr-kodi/repository.fenomscrapers/master/zips/addons.xml</info>
    <checksum>https://raw.githubusercontent.com/mr-kodi/repository.fenomscrapers/master/zips/addons.xml.md5</checksum>
    <datadir zip="true">https://raw.githubusercontent.com/mr-kodi/repository.fenomscrapers/master/zips/</datadir>
</dir>
```
## How to Import Fenom Scrapers Into Any Addon

Any multi-source Kodi addon can be altered to use these new scrapers instead of its own, you can follow the
instructions below to get things updated. When applying to a different addon, change "name_of_addon" with the name
of the addon.

Open the `addons/plugin.video.name_of_addon/addon.xml`.

Add the following line to the addon.xml file:

`<import addon=”script.module.fenomscrapers/>`

Open addons/script.module.name_of_addon/lib/resources/lib/modules/sources.py

Add the following line to the `sources.py` file:

`import fenomscrapers`

Add it right after the line that says:

`import re

You will also need to change a few lines in the def `getConstants(self)` function in `sources.py` file:

Find the line that says:

`from resources.lib.sources import sources`

Comment out that line by adding a pound/hashtag at the beginning like this:

`#from resources.lib.sources import sources`

add the following:

`from fenomscrapers import sources`

Enjoy!
