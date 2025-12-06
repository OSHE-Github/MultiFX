#include <JuceHeader.h>

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new FuzzProcessor();
}
