
# Alfred Password Generator #

Generate secure random passwords from Alfred. Uses `/dev/urandom` as source of entropy.

![Alfred Password Generator Demo][demo]


## Features ##

- Passwords can be generated based on strength or length.
- Offers multiple generators, including based on real words and pronounceable pseudo-words generated with Markov chains.
- Shows the strength of each generated password.
- More convenient that 1Password or the like.
- More dependable than online generators.
- Copies passwords as "concealed" data by default (so clipboard managers don't record them).


## Contents ##

- [Installation](#installation)
- [Usage](#usage)
- [Password strength](#password-strength)
  - [Entropy?](#entropy)
  - [How strong should my passwords be?](#how-strong-should-my-passwords-be)
    - [Displayed strength](#displayed-strength)
    - [How can passwords of the same length have different levels of security?](#how-can-passwords-of-the-same-length-have-different-levels-of-security)
- [Configuration](#configuration)
  - [Open Help](#open-help)
  - [An Update is Available / No Update is Available](#an-update-is-available--no-update-is-available)
  - [Default Password Strength](#default-password-strength)
  - [Default Password Length](#default-password-length)
  - [Strength Bar](#strength-bar)
  - [Generators](#generators)
- [Built-in generators](#built-in-generators)
  - [Active generators](#active-generators)
    - [ASCII Generator](#ascii-generator)
    - [Alphanumeric Generator](#alphanumeric-generator)
    - [Clear Alphanumeric Generator](#clear-alphanumeric-generator)
    - [Numeric Generator](#numeric-generator)
    - [Pronounceable Nonsense Generator](#pronounceable-nonsense-generator)
    - [Dictionary Generator](#dictionary-generator)
  - [Inactive generators](#inactive-generators)
    - [Pronounceable Markov Generator](#pronounceable-markov-generator)
    - [German Generator](#german-generator)
    - [German Alphanumeric Generator](#german-alphanumeric-generator)
    - [German Pronounceable Markov Generator](#german-pronounceable-markov-generator)
- [Custom generators](#custom-generators)
  - [ Examples](#examples)
- [Licensing, thanks](#licensing-thanks)
- [Changelog](#changelog)
  - [Version 1.0 (2015-07-28)](#version-10-2015-07-28)
  - [Version 1.1 (2015-07-28)](#version-11-2015-07-28)
  - [Version 1.2 (2015-07-31)](#version-12-2015-07-31)
  - [Version 1.3 (2015-11-03)](#version-13-2015-11-03)
  - [Version 2.0 (2017-02-26)](#version-20-2017-02-26)
  - [Version 2.0.1 (2017-04-01)](#version-201-2017-04-01)
  - [Version 2.0.2 (2017-04-01)](#version-202-2017-04-01)
  - [Version 2.1 (2017-04-02)](#version-21-2017-04-02)


## Installation ##

Download from the [GitHub releases][gh-releases] or [Packal][packal] and double-click the downloaded file to install.


## Usage ##

- `pwgen [<strength>]` — Generate passwords of specified strength. Default is `3` (96 bits of entropy). See [Password strength](#password-strength) for details.
    - `↩` — Copy the selected password to the clipboard.
    - `⌘↩` — Copy the selected password to the clipboard and paste it to the frontmost application.
    - `⌥↩` or `⌘C` — Copy the selected password to the clipboard *as public data*
    - `^↩` — Copy the selected password to the clipboard *as public data* and paste it to the frontmost application.
    - `⌘+L` — Show the selected password in Alfred's Large Text window.
- `pwlen [<length>]` — Generate passwords of specified length. Default is `20`. See [Password strength](#password-strength) for details.
    - `↩` — Copy the selected password to the clipboard.
    - `⌘↩` — Copy the selected password to the clipboard and paste it to the frontmost application.
    - `⌥↩` or `⌘C` — Copy the selected password to the clipboard *as public data*
    - `^↩` — Copy the selected password to the clipboard *as public data* and paste it to the frontmost application.
    - `⌘+L` — Show the selected password in Alfred's Large Text window.
- `pwconf [<query>]` — View and edit workflow settings. See [Configuration](#configuration) for details.

**Note:** Word-based generators may provide passwords that are slightly longer than `<length>`.


## Password strength ##

Passwords can be specified either by strength or length. The default strength is `3`, which is at least 96 bits of entropy (each level is 32 bits). You may also specify the desired number of bits by appending `b` to your input, e.g. `pwgen 128b` will provide at least 128 bits of entropy.

Default length is 20 characters, which can provide ~50 to ~130 bits of entropy depending on generator.

Each password has its strength in the result subtitle. This is shown either as a bar or in bits of entropy, depending on your settings. Each full block in the bar represents 32 bits of entropy. The icon shown next to each password also reflects its strength:

| Icon                            | Strength (bits of entropy) |
| ------------------------------- | -------------------------- |
| ![](./strong.png "strong.png")  | Strength >= 96b            |
| ![](./okay.png "okay.png")      | Strength > 64b and < 96b   |
| ![](./weak.png "weak.png")      | Strength <= 64b            |


### Entropy? ###

"Entropy" is [cryptographese for "randomness"][entropy].


### How strong should my passwords be? ###

That depends on what you're using it for and how long you want it to remain secure. As of 2015, custom password-guessing hardware (built from standard PC components) can guess **&gt;45 billion passwords per second.**

The *average* number of guesses required to crack a password with *n* bits of entropy is 2<sup>n-1</sup>, so 2,147,483,647 guesses for a 32-bit password. Or **0.048 seconds** with the above hardware.

Fortunately, every added bit doubles the amount of entropy, so 64 bits is a good deal stronger: 6.5 *years* on average to guess on the same hardware.

| Level   | Min. entropy          | Av. time to guess&nbsp;\*                         | Application                               |
| ------: | --------------------: | --------------:                               | ---------------------------               |
| 1       | 32&nbsp;bits          | 0.048 seconds                                 | Stuff you want to be super easy to crack? |
| 2       | 64&nbsp;bits          | 6.5 years                                     | Web accounts, WiFi passwords              |
| 3       | 96&nbsp;bits          | 280 million years                             | Almost anything                           |
| 4       | 128&nbsp;bits         | billions of times the age of the universe | Toppest-secret stuff, e.g. encryption keys&nbsp;\*\*                           |

\* = based on 45 billion guesses per second.
\*\* = *symmetric* encryption keys. SSL certificates, for example, use *asymmetric* keys, which offer much less security per bit. A 1024-bit RSA key has roughly equivalent security to an 80-bit symmetric key.

The default password strength level of 3 (96 bits) provides very secure passwords.

The default password length of 20 characters provides reasonably to very secure passwords, depending on the generator.


#### Displayed strength ####

By default, the strength of generated passwords is shown as a bar in the result subtitle. Each full block represents 32 bits of entropy, so 2 blocks represents a pretty secure password, 3 or more a very secure password.

You can have the precise number of bits displayed instead by toggling the "Strength Bar" setting in the [Configuration](#configuration) (keyword `pwconf`).


#### How can passwords of the same length have different levels of security? ####

Passwords of the same length (or even the self-same password) generated using different techniques have different strengths because the strength is determined by the permutations in the algorithm and the password length, not the password itself.

For example, the single-digit password `1` has an entropy of 3.32 bits when generated by the Numeric algorithm because it is one of only 10 possible one-digit passwords. The same password generated by the ASCII algorithm has an entropy of 5.95 bits because it is one of 62 possible one-character passwords.

Of course, that's just in theory. A password generated by the German generator is theoretically more secure than the same password generated by the ASCII-only one because the former has more possible passwords of any given length. That only holds in practice if an attacker is also guessing passwords based on the German alphabet. If they're guessing based on ASCII, and the password only contains ASCII characters, the password is naturally as easily guessed as if it had been generated by the ASCII generator.

See [Password strength on Wikipedia](https://en.wikipedia.org/wiki/Password_strength#Random_passwords) for more information.


## Configuration ##

Access the configuration options with the `pwconf` keyword. You can use an optional query to filter the available options, e.g. use `pwconf gen` to show only the available generators.

The following configuraton options are available:


### Open Help ###

Action this item to open this README in your browser.


### An Update is Available / No Update is Available ###

The workflow checks for a new version once a day. If one is available, "An Update is Available" will be shown. Action this item to install the update.

If no update is available, "No Update is Available" will be shown. Action this item to force a check for an update.


### Default Password Strength ###

The default strength for passwords generated with `pwgen`. For strength *n*, passwords will have *n*\*32 bits of entropy. Default is `3`, which should be proof against anything but the NSA. `4` will generate extremely secure passwords.

Action this item to enter a new default strength.


### Default Password Length ###

The default length in characters for passwords generated with `pwlen`. The default of `20` provides passwords that are reasonably to very secure, depending on the generator.

Action this item to enter a new default length.


### Strength Bar ###

By default, password strength is indicated by a number of blocks. Each full block represents 32 bits of entropy, so 3 blocks is secure, 4 is very secure. Less that 3 blocks should be avoided.

Alternatively, strength can be shown as the number of bits of entropy.

Action this item to toggle the strength bar on/off.


### Generators ###

All the available generators are listed below the other options.

Active generators have a checked green circle as their icon, inactive ones have an empty red circle icon.

Action a generator to toggle it on or off.

## Built-in generators ##

See [below](#custom-generators) for details of how to add your own custom generators.

The workflow includes 10 built-in generators, of which 6 are active by default. You can activate/deactivate them in the [Configuration](#configuration).

**Note**: Word-based password generators return passwords with their component words joined by hyphens. These hyphens are not included in the calculation of the password strength, so removing them will leave you with a password of the stated strength.


### Active generators ###

These generators are active by default.

#### ASCII Generator ####

Generates passwords based on all ASCII characters, minus a few punctuation marks that can be hard to type, such as \\\`~ (backslash, backtick, tilde).


#### Alphanumeric Generator ####

Generates passwords from ASCII letters and digits. No punctuation.


#### Clear Alphanumeric Generator ####

Generates passwords from ASCII letters and digits, excluding the easily-confused characters lO01 (lowercase L, uppercase O, the digits 1 and 0).


#### Numeric Generator ####

Generates digit-only passwords.


#### Pronounceable Nonsense Generator ####

Generates pronounceable passwords based on nonsense words. Based on [this Stack Overflow answer](http://stackoverflow.com/a/5502875).


#### Dictionary Generator ####

Generates passwords based on the words in `/usr/share/dict/words`.


### Inactive generators ###

These generators are inactive by default. They can be turned on in the [Configuration](#configuration).


#### Pronounceable Markov Generator ####

Generates semi-pronounceable passwords based on Markov chains and the start of *A Tale of Two Cities*.

Has slightly more entropy than the [Pronounceable Nonsense generator](#pronounceable-nonsense-generator), but the passwords aren't quite as pronounceable.


#### Hexadecimal Generator ####

Generate passwords using hexadecimal characters (0-9, a-f).


#### German Generator ####

Generate passwords using the German alphabet, digits and punctuation.


#### German Alphanumeric Generator ####

Generate passwords using the German alphabet and digits without punctuation.


#### German Pronounceable Markov Generator ####

Generates semi-pronounceable passwords based on Markov chains and the start of *Buddenbrooks*.


## Custom generators ##

You can easily add your own custom password generators. These must be placed in the directory `~/Library/Application Support/Alfred 2/Workflow Data/net.deanishe.alfred-pwgen/generators/`. If you put your custom generators in the workflow itself, they will be deleted when the workflow is updated. You can quickly open up the above directory by entering the Alfred-Workflow magic argument `workflow:opendata` as your query, e.g. `pwconf workflow:opendata`.

**Note**: Your generators will be deactivated by default. You must manually activate them using `pwconf` to use them.

Modules containing your custom generators *must* be named `gen_XXX.py`.

Only files matching the pattern `gen_*.py` will be imported.

Your generator classes *must* subclass `generators.PassGenBase` or `generators.WordGenBase`, which are [abstract base classes][abcs], and *must* have `id`, `name`, `description` and `data` properties. These have the following purposes:

|    Property   |                                    Purpose                                    |
|---------------|-------------------------------------------------------------------------------|
| `id`          | Short name for your generator; used internally.                               |
| `name`        | The human-readable name; shown in the configuration.                          |
| `description` | The longer description shown beneath the generator name in the configuration. |
| `data`        | Return a sequence of the characters to generate passwords from.               |


The `data` property is used by the `entropy` property and `password()` method on the `PassGenBase` base class.

`PassGenBase` is designed for character-based passwords, i.e. `data` returns a string or other sequence of single characters. `WordGenBase` is for word-based passwords, i.e. `data` returns a sequence of multi-character strings. The main difference is in the implementation of length-based passwords.

**Important:** `data` must return a sequence (`string`, `list` or `tuple`) *not* a generator or `set`. If `random.choice()` chokes on it, it's no good.


### Examples ###

A generator to produce German passwords (i.e. possibly including letters like 'ü' or 'ä'):

```python

import string
from generators import PassGenBase, punctuation
# punctuation is `string.punctuation` minus a few
# problematic/hard-to-type symbols (e.g. backslash)

class GermanGenerator(PassGenBase):
    """Generate passwords containing umlauts."""

    @property
    def id(self):
        return 'deutsch'

    @property
    def name(self):
        return 'German'

    @property
    def description(self):
        return 'German alphabet, digits and punctuation'

    @property
    def data(self):
        return string.ascii_letters + string.digits + punctuation + 'üäöÜÄÖß'
```

A word-based generator to produce Swedish passwords might look like this:

```python
from generators import WordGenBase

class BorkGenerator(WordGenBase):
    """Bork-bork-bork"""

    @property
    def id(self):
        return 'bork'

    @property
    def name(self):
        return 'Bork'

    @property
    def description(self):
        return 'Borked password generator'

    @property
    def data(self):
        return ['bork', 'bork', 'bork']
```

## Licensing, thanks ##

This workflow is released under the [MIT Licence](http://opensource.org/licenses/MIT), which is included as the LICENCE file.

The code for the Markov chain comes from [a SimonSapin snippet][markov], and the gibberish-generating code is from a [Greg Haskins StackOverflow answer][gibberish].

It is heavily based on the [Alfred-Workflow](https://github.com/deanishe/alfred-workflow) library, also released under the MIT Licence.

The workflow icon is from the [Elusive Icons](https://github.com/aristath/elusive-iconfont) webfont \([licence](http://scripts.sil.org/OFL)\).

The other icons are based on the [Font Awesome](http://fortawesome.github.io/Font-Awesome/) webfont \([licence](http://scripts.sil.org/OFL)\).


## Changelog ##

### Version 1.0 (2015-07-28) ###

Initial release


### Version 1.1 (2015-07-28) ###

- Replace default Markov pronounceable generator with gibberish
- Rename Dictionary generator module
- Add licence and licensing info
- Improve usage description in README
- Add generator descriptions to README
- Add strength bar toggle to configuration
- Improve filtering in configuration

### Version 1.2 (2015-07-31) ###

- Add separate base class for word-based generators
- Add custom (user) generator support
- Refactor built-in generators

### Version 1.3 (2015-11-03) ###

- Change `id_` property of generators to `id`


### Version 2.0 (2017-02-26) ###

- Icons reflect password strength
- Alfred 3 only
- Option to turn notifications off [#3][issue3]
- Fix syntax error [#5][issue5]


### Version 2.0.1 (2017-04-01) ###

- Fix paste [#7][pr7]


### Version 2.0.2 (2017-04-01) ###

- Fix hanging background processes [#4][issue4]
- New icons


### Version 2.1 (2017-04-02) ###

- Default to "concealed" copy so clipboard managers will ignore the passwords


[demo]: https://github.com/deanishe/alfred-pwgen/raw/master/demo.gif "Alfred Password Generator Demo"
[gh-releases]: https://github.com/deanishe/alfred-pwgen/releases
[packal]: http://www.packal.org/workflow/secure-password-generator
[markov]: https://github.com/SimonSapin/snippets/blob/master/markov_passwords.py
[gibberish]: http://stackoverflow.com/a/5502875/356942
[entropy]: https://en.wikipedia.org/wiki/Entropy_(computing)
[abcs]: https://docs.python.org/2.7/library/abc.html#module-abc
[issue1]: https://github.com/deanishe/alfred-pwgen/issues/1
[issue2]: https://github.com/deanishe/alfred-pwgen/issues/2
[issue3]: https://github.com/deanishe/alfred-pwgen/issues/3
[issue4]: https://github.com/deanishe/alfred-pwgen/issues/4
[issue5]: https://github.com/deanishe/alfred-pwgen/issues/5
[pr6]: https://github.com/deanishe/alfred-pwgen/pulls/6
[pr7]: https://github.com/deanishe/alfred-pwgen/pulls/7
