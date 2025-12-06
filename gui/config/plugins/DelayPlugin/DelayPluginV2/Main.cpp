#include <JuceHeader.h>
#include "DelayPluginV2.h" // Make sure to update this line with current version

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new DelayProcessor();
}