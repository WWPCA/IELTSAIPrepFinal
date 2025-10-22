# How to Change Nameservers to Custom DNS in Namecheap

## Step 1: Navigate to Nameserver Settings
1. In your Namecheap domain dashboard for ieltsaiprep.com
2. Look for **"Nameservers"** section (usually on the main domain management page)
3. You should see it's currently set to **"Namecheap BasicDNS"**

## Step 2: Change to Custom DNS
1. Click the dropdown next to nameservers
2. Select **"Custom DNS"** from the options
3. This will show 4-5 empty nameserver fields

## Step 3: Leave Fields Empty (For Now)
- Don't enter any nameservers yet
- Leave all nameserver fields blank
- Click **"Save Changes"** or checkmark button

## Step 4: Verify Change
- The nameserver type should now show **"Custom DNS"**
- All DNS record management in Namecheap becomes disabled
- You're ready for Route 53 nameservers

## Alternative Location
If you don't see nameservers on the main page:
- Look for **"Advanced DNS"** tab
- Or **"Domain"** → **"Nameservers"** in the left menu
- Some Namecheap layouts show it under **"DNS"** settings

## What This Does
- Switches from Namecheap's DNS servers to custom ones
- Prepares the domain for Route 53 nameserver integration
- Disables Namecheap DNS record management