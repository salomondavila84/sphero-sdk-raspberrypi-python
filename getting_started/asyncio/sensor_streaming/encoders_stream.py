import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import asyncio
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import SerialAsyncDal
from sphero_sdk import RvrStreamingServices
from sphero_sdk import RawMotorModesEnum


loop = asyncio.get_event_loop()

rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)


async def encoder_handler(encoder_data):
    await rvr.reset_yaw()
    
    encoder_counts = await rvr.get_encoder_counts()
    print(encoder_counts)
    print(encoder_data)
    
    # Forward
    await rvr.raw_motors(
        left_mode=RawMotorModesEnum.forward.value,
        left_duty_cycle=36,  # Valid duty cycle range is 0-255
        right_mode=RawMotorModesEnum.forward.value,
        right_duty_cycle=36  # Valid duty cycle range is 0-255
    )
    
    encoder_counts = await rvr.get_encoder_counts()
    print(encoder_counts)
    print(encoder_data)
    
    # Delay to allow RVR to spin motors
    await asyncio.sleep(2)
    
    # Reverse
    await rvr.raw_motors(
        left_mode=RawMotorModesEnum.reverse.value,
        left_duty_cycle=36,  # Valid duty cycle range is 0-255
        right_mode=RawMotorModesEnum.reverse.value,
        right_duty_cycle=36  # Valid duty cycle range is 0-255
    )
    
    encoder_counts = await rvr.get_encoder_counts()
    print(encoder_counts)
    print(encoder_data)
    
    # Delay to allow RVR to spin motors
    await asyncio.sleep(1)

async def main():
    """ This program demonstrates how to enable multiple sensors to stream.
    """

    await rvr.wake()

    # Give RVR time to wake up
    await asyncio.sleep(2)

    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.encoders,
        handler=encoder_handler
    )

    await rvr.sensor_control.start(interval=250)

    # The asyncio loop will run forever to allow infinite streaming.


if __name__ == '__main__':
    try:
        asyncio.ensure_future(
            main()
        )
        # ToDo: Set motor control here or in another function called upon in loop
        loop.run_forever()

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')

        loop.run_until_complete(
            asyncio.gather(
                rvr.sensor_control.clear(),
                rvr.raw_motors(
                        left_mode=RawMotorModesEnum.off.value,
                        left_duty_cycle=0, # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.off.value,
                        right_duty_cycle=0# Valid duty cycle range is 0-255
                ),
                rvr.close()
            )
        )

    finally:
        if loop.is_running():
            loop.close()
