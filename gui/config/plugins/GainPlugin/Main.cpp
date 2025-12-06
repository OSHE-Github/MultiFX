#include <JuceHeader.h>
#include "GainPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new GainProcessor();
}
