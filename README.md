# Setup:

## Download:
  1) Install docker https://www.docker.com/community-edition#download 
  2) Install docker compose https://docs.docker.com/compose/install/#install-compose
 
## Instantiate the App/Link the Containers:
  1) Navigate to the unzipped directory
  2) Run “docker-compose up” in the terminal

## Pollworkers
  1) A pollworker user is needed in order to check users in - press login in the top right
  2) Select Sign Up in the bottom right of the form
  3) Enter the credentials, along with a precinct ID that you are a pollworker for.  You can only check users into your precinct - we will check!
  4) Sign in every time you need to with the login button in the top right
  5) Setup the printer - see the printer section below
  6) When voting:
    - Go to the top left and select dash - this is where you will check voters in
    - Select your precinct and the election that people will vote in
    - When searching a voter, ask for their name, first and last
    - Should they not know their voter number, hopefully they know the last 4 digits so you can confirm identity (note you will also have an ID).  However, should this not be the case, address can be checked on the admin site by a pollworker administrator.  This is strongly discouraged!
    - A QR code should print when the serial code is accessed - if this is untrue, make sure the printer is set up correct
    - Inform the voter to go to a voting station and scan their QR code in order to vote.  Furthermore, a primary or general should be selected

## Voter Setup
  1) Select the vote screen in the top left
  2) That's literally it

## Printer
  1) Go to the host_script directory within the project with `cd host_scripts`
  2) Open the printAdafruit.py file with your favorite text editor
  3) Depending on the printer, uncomment a line:
    - If you have the blue printer, ensure the line `p = Usb(0x456, 0x0808, 0, 0x81, 0x03)` is uncommented and the other commented
    - If you have the black printer, ensure the line `p = Usb(0x416, 0x5011)` is uncommented and the other commented
    - Note that the blue printer is superior so some functionality might be lacking on the black printer.  Please use the blue printer for all of our sakes.
    - Should NO PRINTER be present, comment out every line that sart with `p.`
    - Should you have problems, be sure the printer paper is facing the right way (the tongue unrolls up)
  4) Plug printer into USB
  5) Run code with `sudo python printAdafruit.py` 
    - Note it's python3 so might have to use `python3` depending on system setup
    - Also note that `sudo` is necessary to access USB (on Linux)
    - Be sure to `pip install` whatever modules you don't have
  6) Watch your printer print stuff!  
    - The site automatically pulls the client IP and uses to print
    - The printer will correctly set up the IP to use your IP

