import adi
import argparse

def main(uri):
	swiot = adi.swiot(uri)
	if swiot is None:
		raise ConnectionError(f"Could not connect to SWIOT1L at {uri}")

	swiot.mode = "config"

	swiot = adi.swiot(uri)
	swiot.ch0_device = "ad74413r"
	swiot.ch0_function = "resistance"
	swiot.ch0_enable = 1
	swiot.ch1_device = "ad74413r"
	swiot.ch1_function = "current_out"
	swiot.ch1_enable = 1

	swiot.mode = "runtime"

	ad74413r = adi.ad74413r(uri)

	# print(ad74413r.channel["resistance0"].sampling_frequency_available)
	ad74413r.channel["resistance0"].sampling_frequency = 1200

	scale = ad74413r.channel["current1"].scale

	while True:
		R = ad74413r.channel["resistance0"].processed / 1000 # mohm -> ohm
		x = R / 40e3    # Map to 0 - 1. Tweak constant depending on the actual potentiometer
		x = min(max(0, x), 1) # Clamp to 0 - 1
		x = 1 - x # Optionally, flip measurement around, in case potentiometer and actuator directions are opposite
		x = x * 16 + 4  # Map to 4 - 20 mA

		print(f'{R=:.1f} ohm\t{x=:.1f} mA')

		ad74413r.channel["current1"].raw = int(x / scale)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='SWIOT1L demo: Read a 50k potentiometer on channel 1, send out a proportional 4-20 mA signal on channel 2.')
	parser.add_argument('-u', '--swiot1l_uri', default='ip:169.254.97.40')
	args = vars(parser.parse_args())

	uri = args['swiot1l_uri']

	main(uri)
