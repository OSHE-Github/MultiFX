#include <JuceHeader.h>
#include "FlangerPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new FlangerProcessor();
}
