#include <JuceHeader.h>
#include "FunDistortionPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new FunDistortionProcessor();
}
