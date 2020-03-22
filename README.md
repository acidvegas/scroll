# scroll
> Scroll is full-featured IRC bot that carries a **PENIS PUMP** & will brighten up all the mundane chats in your lame IRC channels with some colorful IRC artwork! Designed to be extremely stable, this bot is sure to stay rock hard & handle itself quite well!

![](screens/preview.png)

## Requirements
- [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python)*

## Setup
Edit the [core/config.py](scroll/core/config.py) file and then place your art files in the [art](scroll/art) directory.

This repository by itself does not contain any art. A large organized collection of IRC art can be cloned from the [ircart](https://github.com/ircart/ircart) repository directory into your [data/art](scroll/data/art) directory:

`git clone https://github.com/ircart/ircart.git $SCROLL_DIR/scroll/art` *(change the `$SCROLL_DIR` to where you cloned it)*

**Warning:** Try not to have any filenames in your [art](scroll/art) directory that are the same as any of the [Commands](#commands) below or you won't be able to play them!

## Commands
### User Commands
| Command                         | Description                                                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| @scroll                         | information about scroll                                                                                                                         |
| .ascii dirs                     | list of ascii directories                                                                                                                        |
| .ascii list                     | list of ascii filenames                                                                                                                          |
| .ascii random [dir]             | play random art, optionally from the [dir] directory only                                                                                        |
| .ascii search \<query>          | search [data/art](scroll/data/art) for \<query>                                                                                                  |
| .ascii stop                     | stop playing art                                                                                                                                 |
| .ascii \<name> [\<trunc>]       | play \<name> art from [data/art](scroll/data/art) *(see usage below)*                                                                            |

#### Note
The \<trunc> argument for the `.ascii` command allows you to truncate lines off of an ASCII. The data is TOP,BOTTOM,LEFT,RIGHT,SPACES. Top being how many lines to remove from the top. Bottom being the same except from the bottom. Left and right remove characters from each side, and spaces will prefix lines with this many spaces.

**Example:** `.ascii funnyguy 3,5,0,10,30` *(This will remove 3 lines from the top, 5 lines from the bottom, no characters from the left, 10 characters from the right, and append 30 spaces before each line)*

### Admin Commands *(Private Message)*
| Command                       | Description                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------- |
| .config [\<setting> \<value>] | view config or change \<setting> to \<value>                                                        |
| .ignore [\<add/del> \<ident>] | view ignore list or \<add/del> an \<ident> *(must be in nick!user@host format, wildcards accepted)* |
| .raw \<data>                  | send \<data> to the server                                                                          |
| .update                       | update the [data/art](scroll/data/art) directory *(see usage below)*                                |

#### Note
The `.update` command is if you cloned a git repository, like the one mentioned in the [Setup](#setup) section, for your [art](scroll/art) directory. This will simply perform a `git pull` on the repository to update it.

## Config Settings
| Setting         | Description                                                                           |
| --------------- | ------------------------------------------------------------------------------------- |
| max_lines       | maximum number of lines an art can be to be played outside of the **#scroll** channel |
| max_results     | maximum number of results returned from a search                                      |
| throttle_cmd    | command usage throttle in seconds                                                     |
| throttle_msg    | message throttle in seconds                                                           |
| rnd_exclude     | directories to ignore with `.ascii random`. *(comma-seperated list)*                  |

## Screens
This section is not finished. Screens will be added soon.

## Todo
* Improve truncation of the left and right by retaining the last known color code.
* Add ascii tagging to database. Lets you tag asciis with hashtags for searching. Maybe include an author tag also.
* Add an ascii amplification factor and zigzag to the trunc array, and maybe rename trunc to morph.
* Controls for admins to move, rename, delete, and download ascii on the fly.

## Mirrors
- [acid.vegas](https://acid.vegas/scroll) *(main)*
- [GitHub](https://github.com/ircart/scroll)
- [GitLab](https://gitlab.com/ircart/scroll)