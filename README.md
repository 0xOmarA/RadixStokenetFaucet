# The Radix Stokenet Faucet

Welcome to the GitHub repository of the the Radix Stokenet Faucet. This faucet is a community effort built with the Django web-framework and the RadixLib Python library. 

This is an authenticated faucet which is built in a similar way to Ethereum's Rinkeby faucet. In order for a user to get funded, the user needs to make a tweet with their wallet address and then provide a link to the tweet to the faucet. The funds would then be sent to the wallet that the user provided and a cooldown would then be imposed on both the wallet address and the twitter account.

## Setting up your own faucet

You can setup your own faucet if you so choose using this Django project. This portion of the documentation is written with the assumption that you're familiar with how Django projects can be deployed. If not, then you can view [this](https://www.digitalocean.com/community/tutorials/how-to-deploy-django-to-app-platform) guide or [this](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04) guide to learn more.

First of all, begin by cloning this directory to your local machine or to the instance you will be using to run the faucet. 
```shell
git clone https://github.com/0xOmarA/RadixStokenetFaucet
cd RadixStokenetFaucet
```

If you are on linux, then there are a few packages that you need to install first before installing the project's dependencies
```shell
sudo apt-get install gcc python3-dev
```

You now need to create a virtual environment to install the project dependencies in. 
```shell
python3 -m venv env
source ./env/bin/activate
```

With the virtual envirnoment created and activated, you can now install the project dependencies
```shell
pip3 install -r requirements.txt
```

You now have all of the needed packages to run the project. However, you're still missing one important file which is the `secrets.py` file. This file contains information that the project needs to run such as the django secret key, your wallet's mnemonic phrase, and your twitter API keys.

Create a new file called `secrets.py` inside the `faucet_proj` directory such that the `faucet_proj` has the following structure:
```
faucet_proj
	|-__init__.py
	|-__pycache__
	|-asgi.py
	|-faucet_option.py
	|-secrets.py
	|-settings.py
	|-urls.py
	|-wsgi.py
```

The following is a sample `secrets.py` file. Keep in mind that the information and details provided in this sample file is not real. You will need to populate the `secrets.py` file with your own personal information
```python
mnemonic_phrase: str = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
""" The mnemonic phrase to use for the wallet which distributes the XRD tokens """

twitter_bearer_token: str = "MySuperSecretKey"
""" The bearer token to use when making requests to the Twitter API. """

django_secret_key: str = 'MySuperDuperUltraSecretKey'
""" The django secret key used to encrypt the data in Django """
```

Once you have created and populated your `secrets.py` file, you're now ready to run and eventually deploy your faucet to the internet. To test your faucet, run the following command:
```python
python3 manage.py runserver
```

You can now visit your own faucet on the [localhost](http://localhost).

## How to use the faucet
Using this faucet is extremely simple. Follow the steps below in order to get some XRD sent to your Stokenet address:
* Make a tweet containing your Stokenet wallet address.
* Copy the address to your tweet.
* Visit http://www.StokenetFaucet.com and paste the link to your tweet in the provided field.
* Select the amount of XRD that you would like.
* Click on the **Request** button.

Throughout this process, you will be guided by the messages that will appear if an error has occured.

## How to help

There are many ways in which you can help this project out:

* Directly supporting and helping maintain the codebase and helping add additional features to the site.
* Eventually, the XRD in my Stokenet wallet will run out and the faucet will be dried out... If you have some extra Stokenet XRD, please send them to this address: `tdx1qspqqecwh3tgsgz92l4d4f0e4egmfe86049dj75pgq347fkkfmg84pgx9um0v`. The Stokenet XRD you send to this address will be used to send XRD to other users.