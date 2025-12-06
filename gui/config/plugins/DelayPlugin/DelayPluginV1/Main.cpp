#include <JuceHeader.h>
//#include <juce_DelayLine.h>
#include "DelayPluginV1.h" //make sure to update this for each new version!

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new DelayProcessor();
}

//note: juce_dsp module added