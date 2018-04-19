# Download:
 1) Install docker https://www.docker.com/community-edition#download 
 2) Install docker compose https://docs.docker.com/compose/install/#install-compose
 
# Instantiate the App/Link the Containers:
 1) Navigate to the unzipped directory
 2) Run “docker-compose up” in the terminal

# Setup:

## Printer
 1) Go to the host_script directory within the project with `cd host_scripts`
 2) Open the printer.py file with your favorite text editor
 3) Depending on the printer, uncomment a line:
   - If you have the blue printer, ensure the line `p = Usb(0x456, 0x0808, 0, 0x81, 0x03)` is uncommented and the other commented
   - If you have the black printer, ensure the line `p = Usb(0x416, 0x5011)` is uncommented and the other commented
   - Note that the blue printer is superior so some functionality might be lacking on the black printer
   - Should NO PRINTER be present, comment out every line that sart with `p.`
 4) Plug printer into USB
 5) Run code with `sudo python printer.py` 
   - Note it's python3 so might have to use `python3` depending on system setup
   - Also note that `sudo` is necessary to access USB (on Linux)
 6) Watch your printer print stuff!  
   - The site automatically pulls the client IP and uses to print
   - The printer will correctly set up the IP to use your IP

