#include <JuceHeader.h>
#include "DelayPluginV3.h" // Make sure to update this line with current version

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new DelayProcessor();
}