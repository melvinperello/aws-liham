https://github.com/rotati/wiki/wiki/Git:-Combine-all-messy-commits-into-one-commit-before-merging-to-Master-branch

# Git: Combine all messy commits into one commit before merging to Master branch

Assume we have a new branch name **capistrano-configuration** which is branched out from **Master**. Inside **capistrano-configuration** branch, there are a lot of messy commits as we change a piece of code many times and deploy to the staging server with **cap staging deploy** command. 

Once we type `git log`, the commit logs will be:

```
commit 8eb3a6e68a2453e602c346d43f0c1229dc159221
Author: Someth Victory <victory.someth@gmail.com>
Date:   Tue Aug 25 14:09:31 2015 +0700

    Remove unused code

commit 59e4f4290e0940da42a66673cfc026e5c8e735c9
Author: Someth Victory <victory.someth@gmail.com>
Date:   Tue Aug 25 10:57:25 2015 +0700

    Change some config and update style

commit 2bf99e1d42e769e9e4029da1139cde1d83523b3e
Author: Someth Victory <victory.someth@gmail.com>
Date:   Tue Aug 25 09:48:33 2015 +0700

    Update stylesheet

commit 8781bc74904c7b986d6ead74272fce48837b06a3
Author: Someth Victory <victory.someth@gmail.com>
Date:   Tue Aug 25 09:30:04 2015 +0700

    Update font color to black

commit 423dc810588270ac23878493b143c55c8856b8dc
Author: Someth Victory <victory.someth@gmail.com>
Date:   Tue Aug 25 09:24:15 2015 +0700

    Update import stylesheet

commit d366250fe6db29bd744e006629806b770da68173
Author: Someth Victory <victory.someth@gmail.com>
Date:   Mon Aug 24 17:32:33 2015 +0700

    Update style
```

As you see that the commit logs are very messy and meaningless. We still actually could merge **capistrano-configuration** into **master**, but it's not a good practice as it will pollute the commit message in **master**. 

The ideal solution is to combine all the commits into only one meaningful commit message.

### Step 1: Create another branch from the latest **master**

Assume that you are on your latest master branch.

```
git checkout -b capistrano-config
```

### Step 2: Merge **capistrano-configuration** into **capistrano-config** with --squash option

```
git checkout capistrano-config
git merge --squash capistrano-configuration
git commit # without -m 
```

An editor should be popup with all the commit logs, and files changed from **capistrano-configuration**. 
You could actually delete everything, and write only one line of the commit message you want to show after merging into **master**. In this case, we write "Setup Capistrano Configuration". Save and quite the editor.

### Step 3: Merge your newly created branch into master

Last but not least, you could actually merge **capistrano-config** into master now.

```
git checkout master
git merge capistrano-config
```

You are done!

When you type `git log` in your **master** branch, it will show the following logs:

```
commit 2a5853e36e0ddc20ad52aef44ec1da8666ae6cf8
Author: Someth Victory <victory.someth@gmail.com>
Date:   Tue Aug 25 14:43:42 2015 +0700

    Setup staging configuration

commit f835f98ed5e49b1ad262236f319c9bc1881ffa68
Author: Uysim <uysimty@gmail.com>
Date:   Fri Aug 14 11:32:59 2015 +0700

    Fix some style

commit 5c275c060c1f7288f281d5343114729b50432812
Author: Someth Victory <victory.someth@gmail.com>
Date:   Fri Aug 14 09:20:26 2015 +0700

    Update README.md
```

Now you get only one meaningful commit message in the **master** branch.
